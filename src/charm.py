#!/usr/bin/env python3
# Copyright 2022 ootao
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

import logging
import subprocess
import time
import os

from ops.framework import StoredState
from ops.main import main
from ops.charm import ActionEvent,CharmBase,StartEvent
from ops.model import ActiveStatus, MaintenanceStatus

logger = logging.getLogger(__name__)


class DemoCharm(CharmBase):
    # Note: self._stored can only store simple data types (int/float/dict/list/etc)
    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self._stored.set_default(
            things={},
            config={},
            charm_initialized=False,
        )

        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.install, self._on_install)
        self.framework.observe(self.on.start, self._on_start)
        self.framework.observe(self.on.debug_action, self._on_action_debug)
        self.framework.observe(self.on.test_fortune_action, self._on_action_test_fortune)

    def _on_config_changed(self, event) -> None:
        logger.info("Updating charm config")

        self._stored.things["alice"] = self.model.config["alice"]
        self._stored.things["bobob"] = self.model.config["bobob"]
        sta_message = self.model.config['message']

        self.unit.status = ActiveStatus(sta_message)
        logger.debug("Configuration change(s) applied successfully")

    def _on_install(self, event) -> None:
        logger.info("Installing the Demo charm")

        try:
            # 创建一个目录
            # path = "/home/ootao/Documents/tmp"
            path = "."
            time_now = time.localtime()
            folder = path + "/" + time.strftime("%Y-%m-%d", time_now)
            
            b = subprocess.run(["ls", "/home"], capture_output=True)
            logger.debug("LS_HOME:" + b.stdout.decode())

            if not os.path.exists(folder):
                os.mkdir(folder)
                logger.info(folder + ' 创建成功')
            else:
                logger.info(folder + ' 目录已存在')

            self._stored.things["folder"] = folder
            self._stored.charm_initialized = True
            logger.info("Demo initialized successfully")
        except RuntimeError:
            logger.error("Failed to install Demo")
            event.defer()
            return

        self.unit.status = MaintenanceStatus("Installation done")

    def _on_start(self, event: StartEvent) -> None:
        logger.info("Starting the Demo charm")

        if not self._stored.charm_initialized:
            logger.info("DemoCharm is not initialized yet, not starting the charm")
            return

        # 用时间戳创建个文件
        path = self._stored.things["folder"]
        if not os.path.exists(path):
            logger.info(path + '目录不存在')
            return 
        else:
            time_now = time.localtime()
            foldername = time.strftime("%Y-%m-%d-%H_%M_%S", time_now) + ".txt"
            with open(path + '/' + foldername, 'w') as f:
                f.write("this is a simple test")

        self.unit.status = ActiveStatus("Start")

    def _on_action_debug(self, event: ActionEvent) -> None:
        try:
            # 执行打印日志命令
            b = subprocess.run(["history"], capture_output=True, check=True, timeout=600)
        except subprocess.CalledProcessError as e:
            msg = f'Failed to run "{e.cmd}": {e.stderr} ({e.returncode})'
            event.fail(msg)
            logger.error(msg)
            raise RuntimeError

        event.set_results({"buginfo": b.stdout})
        logger.debug("buginfo called successfully")

    def _on_action_test_fortune(self, event: ActionEvent) -> None:
        some = event.params.get("some")
        fail = event.params.get("fail")

        is_successed = False
        # TODO do something
        if is_successed:
            msg = f"the value of SOME field: \n{some}"
            event.set_results({"result": msg})
        else:
            msg = f"the value of FAIL field: \n{fail}"
            event.fail(msg)
            logger.error(msg)

    def config_changed(self) -> dict:
        """Figure out what changed."""
        new_config = self.config
        old_config = self._stored.config
        apply_config = {}
        for k, v in new_config.items():
            if k not in old_config:
                apply_config[k] = v
            elif v != old_config[k]:
                apply_config[k] = v

        return apply_config


if __name__ == "__main__":
    main(DemoCharm)
